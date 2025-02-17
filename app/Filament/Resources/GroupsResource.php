<?php

namespace App\Filament\Resources;

use App\Filament\Resources\GroupsResource\Pages;
use App\Filament\Resources\GroupsResource\RelationManagers;
use App\Models\Groups;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletingScope;
use Illuminate\Support\Facades\DB;


class GroupsResource extends Resource
{
    protected static ?string $model = Groups::class;
    protected static ?string $navigationGroup = 'Menu';
    protected static ?string $navigationIcon = 'heroicon-o-rectangle-group';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                //
                Forms\Components\TextInput::make('menugrouptext')
                ->label('Grupo')
                ->required()
                ->maxLength(14)
                ->dehydrateStateUsing(fn (string $state) => strtoupper($state))
                ->rule(function (string $operation, ?Model $record = null) {
                    return function ($attribute, $value, $fail) use ($operation, $record) {
                        if ($value !== null) {
                            $query = DB::table('groups')
                                ->where('menugrouptext', $value);
                            if ($operation === 'edit' && $record) {
                                $query->where('id', '!=', $record->id);
                            }
                            $exists = $query->exists();
                            if ($exists) {
                                $fail('El nombre ya está en uso. Debe ser único.');}
                        }
                    };
                }),
                Forms\Components\Toggle::make('menugroupinactive')
                ->label('Inactivo')
                ->required()
                ->inline(false)
                ->reactive()
                ->afterStateUpdated(fn ($state, Forms\Set $set) => $set('displayindex', $state ? -1 : null)),
                Forms\Components\Select::make('displayindex')
                ->label('Posicion')
                ->required()
                ->options(function (string $operation, ?Model $record = null) {
                    $query = DB::table('groups')
                        ->where('menugroupinactive', '!=', true)
                        ->pluck('displayindex');
                    if ($operation === 'edit' && $record) {
                        $query = $query->filter(fn ($value) => $value != $record->displayindex);
                    }
                    $allPossibleValues = range(-1, 31);
                    $availableValues = collect($allPossibleValues)
                        ->filter(function ($value) use ($query) {
                            return !$query->contains($value);
                        })
                        ->mapWithKeys(function ($value) {
                            return [$value => $value === -1 ? 'Inactivo (-1)' : "Posición {$value}"];
                        })
                        ->toArray();

                    return $availableValues;
                })
                ->searchable()
                ->preload(),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                //
                Tables\Columns\TextColumn::make('id'),
                Tables\Columns\TextColumn::make('menugrouptext')
                ->label('Grupo')
                ->searchable(),
                Tables\Columns\TextColumn::make('displayindex')
                ->label('Posicion')
                ->sortable(),
                Tables\Columns\CheckboxColumn::make('menugroupinactive')
                ->label('Inactivo')
                ->disabled()
                ->sortable()
            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListGroups::route('/'),
            'create' => Pages\CreateGroups::route('/create'),
            'edit' => Pages\EditGroups::route('/{record}/edit'),
        ];
    }
    public static function getModelLabel(): string
    {
        return __(key: 'Grupo');
    }
    public static function getPluralModelLabel(): string
    {
        return __(key: 'Grupos');
    }
}
