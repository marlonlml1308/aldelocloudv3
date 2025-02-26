<?php

namespace App\Filament\Resources;

use App\Filament\Resources\PaymenttypesResource\Pages;
use App\Filament\Resources\PaymenttypesResource\RelationManagers;
use App\Models\Paymenttypes;
use Filament\Forms;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletingScope;
use Illuminate\Support\Facades\DB;

class PaymenttypesResource extends Resource
{
    protected static ?string $model = Paymenttypes::class;

    protected static ?string $navigationIcon = 'heroicon-o-wallet';
    protected static ?string $navigationGroup = 'Configuracion';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                TextInput::make('name')
                ->label('Grupo')
                ->required()
                ->maxLength(14)
                // ->dehydrateStateUsing(fn (string $state) => strtoupper($state))
                ->rule(function (string $operation, ?Model $record = null) {
                    return function ($attribute, $value, $fail) use ($operation, $record) {
                        if ($value !== null) {
                            $query = DB::table('payment_types')
                                ->where('name', $value);
                            if ($operation === 'edit' && $record) {
                                $query->where('id', '!=', $record->id);
                            }
                            $exists = $query->exists();
                            if ($exists) {
                                $fail('El nombre ya está en uso. Debe ser único.');}
                        }
                    };
                }),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                TextColumn::make('id'),
                TextColumn::make('name')
                ->label('Nombre')
                ->searchable(),
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
            'index' => Pages\ListPaymenttypes::route('/'),
            'create' => Pages\CreatePaymenttypes::route('/create'),
            'edit' => Pages\EditPaymenttypes::route('/{record}/edit'),
        ];
    }
    public static function getModelLabel(): string
    {
        return __(key: 'Medio de Pago');
    }
    public static function getPluralModelLabel(): string
    {
        return __(key: 'Medios de Pago');
    }
}
