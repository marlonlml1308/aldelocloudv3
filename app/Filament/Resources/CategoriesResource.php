<?php

namespace App\Filament\Resources;

use App\Filament\Resources\CategoriesResource\Pages;
use App\Filament\Resources\CategoriesResource\RelationManagers;
use App\Models\Categories;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletingScope;
use Illuminate\Support\Facades\DB;

class CategoriesResource extends Resource
{
    protected static ?string $model = Categories::class;
    protected static ?string $navigationGroup = 'Menu';
    protected static ?string $navigationIcon = 'heroicon-o-rectangle-stack';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                //
                Forms\Components\TextInput::make('menucategorytext')
                ->label('Categoria')
                ->required()
                ->maxLength(14)
                ->dehydrateStateUsing(fn (string $state) => strtoupper($state))
                ->rule(function (string $operation, ?Model $record = null) {
                    return function ($attribute, $value, $fail) use ($operation, $record) {
                        if ($value !== null) {
                            $query = DB::table('categories')
                                ->where('menucategorytext', $value);
                            if ($operation === 'edit' && $record) {
                                $query->where('id', '!=', $record->id);
                            }
                            $exists = $query->exists();
                            if ($exists) {
                                $fail('El nombre ya está en uso. Debe ser único.');}
                        }
                    };
                }),
                Forms\Components\Toggle::make('menucategoryinactive')
                ->label('Inactivo')
                ->required()
                ->inline(false),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                //
                Tables\Columns\TextColumn::make('id'),
                Tables\Columns\TextColumn::make('menucategorytext')
                ->label('Categoria')
                ->searchable(),
                Tables\Columns\CheckboxColumn::make('menucategoryinactive')
                ->label('Inactivo')
                ->disabled()
            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    // Tables\Actions\DeleteBulkAction::make(),
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
            'index' => Pages\ListCategories::route('/'),
            'create' => Pages\CreateCategories::route('/create'),
            'edit' => Pages\EditCategories::route('/{record}/edit'),
        ];
    }

    public static function getModelLabel(): string
    {
        return __(key: 'Categoria');
    }
    public static function getPluralModelLabel(): string
    {
        return __(key: 'Categorias');
    }
}
